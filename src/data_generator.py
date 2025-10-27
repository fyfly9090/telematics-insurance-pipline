"""
Synthetic telematics generator (events CSV).
Outputs columns:
  driver_id, trip_id, event_id, timestamp, lat, lon, speed_kmh, accel_ms2

Usage:
  python src/data_generator.py --n-drivers 500 --days 60 --out data/simulated_telematics.csv --seed 42
"""
import argparse
import random
import csv
from datetime import datetime, timedelta, timezone
import itertools
import uuid

def random_trip(start_ts, mean_length_min=15, min_interval_s=5, max_interval_s=10,
                inject_harsh_prob=0.02):
    """
    Return list of points: each point is dict with keys:
      timestamp (ISO UTC), speed_kmh, accel_ms2, lat, lon
    """
    pts = []
    # expected number of points (Poisson-like): ensure at least 3
    n = max(3, int(random.expovariate(1.0 / mean_length_min)))
    ts = start_ts
    speed = random.uniform(0, 30)  # starting speed km/h (0-30)
    base_lat = 42.35
    base_lon = -71.08

    for i in range(n):
        # variable interval between samples
        delta_s = random.randint(min_interval_s, max_interval_s)
        ts = ts + timedelta(seconds=delta_s)

        # sometimes inject a harsh event (rare)
        if random.random() < inject_harsh_prob:
            # simulate sudden braking
            accel = random.uniform(-6.0, -3.0)  # strong negative acceleration
            speed = max(0, speed + accel * (delta_s / 1.0))  # rough integrate accel -> speed
        else:
            # smooth speed evolution
            speed += random.gauss(0, 2)
            speed = max(0, min(160, speed))

            # acceleration (m/s^2) approximate (converted from delta speed km/h)
            accel = random.gauss(0, 0.8)

        # small correlated lat/lon drift per point
        lat = base_lat + random.uniform(-0.05, 0.05)
        lon = base_lon + random.uniform(-0.05, 0.05)

        pts.append({
            "timestamp": ts.replace(tzinfo=timezone.utc).isoformat(),
            "speed_kmh": round(speed, 2),
            "accel_ms2": round(accel, 3),
            "lat": round(lat, 6),
            "lon": round(lon, 6)
        })
    return pts

def generate_driver_rows(driver_id, start_date, days, trips_per_day_mean=2, min_trips_per_day=0):
    """Generate list of event rows for a single driver for 'days' days."""
    rows = []
    trip_counter = 0
    for d in range(days):
        day = start_date + timedelta(days=d)
        # trips per day with small variance
        trips_today = max(min_trips_per_day, int(round(random.gauss(trips_per_day_mean, 1))))
        for _ in range(trips_today):
            # random trip start time in the day
            start_ts = day + timedelta(hours=random.randint(0,23), minutes=random.randint(0,59), seconds=random.randint(0,59))
            trip_id = f"{driver_id}_trip_{trip_counter}"
            trip_counter += 1
            trip_pts = random_trip(start_ts)
            # convert to rows and include event ids
            for ev_i, p in enumerate(trip_pts):
                rows.append({
                    "driver_id": driver_id,
                    "trip_id": trip_id,
                    "event_id": str(uuid.uuid4()),
                    "timestamp": p["timestamp"],
                    "lat": p["lat"],
                    "lon": p["lon"],
                    "speed_kmh": p["speed_kmh"],
                    "accel_ms2": p["accel_ms2"]
                })
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-drivers", type=int, default=500)
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--out", type=str, default="../data/simulated_telematics.csv")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--trips-per-day-mean", type=float, default=2.0)
    parser.add_argument("--min-trips-per-day", type=int, default=0)
    parser.add_argument("--inject-harsh-prob", type=float, default=0.02)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    start_date = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=args.days)
    header = ["driver_id","trip_id","event_id","timestamp","lat","lon","speed_kmh","accel_ms2"]
    with open(args.out, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for i in range(args.n_drivers):
            did = f"driver_{i:04d}"
            rows = generate_driver_rows(did, start_date, args.days,
                                        trips_per_day_mean=args.trips_per_day_mean,
                                        min_trips_per_day=args.min_trips_per_day)
            for r in rows:
                writer.writerow(r)
    print(f"Wrote simulated telematics to {args.out} (drivers={args.n_drivers}, days={args.days})")

if __name__ == "__main__":
    main()

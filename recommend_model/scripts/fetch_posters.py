"""
Standalone script to enrich movies dataset with TMDB poster paths.
"""

import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Load API key
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Input / Output files
input_file = "recommend_model/data/processed/movies_cleaned.csv"
output_file = "recommend_model/data/processed/movies_with_posters.csv"
failed_file = "recommend_model/data/processed/failed_posters.csv"

# Ensure output directories exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)
os.makedirs(os.path.dirname(failed_file), exist_ok=True)

# Smart loading: Resume from existing progress or start fresh
if os.path.exists(output_file):
    print("Found existing progress file. Resuming from where we left off...")
    df = pd.read_csv(output_file)
    existing_posters = df['poster_path'].notna().sum()
    print(f"Loaded {len(df)} movies with {existing_posters} existing posters")
else:
    print("No existing progress found. Starting fresh...")
    df = pd.read_csv(input_file)
    if "poster_path" not in df.columns:
        df["poster_path"] = None

# Show remaining work
remaining_work = df['poster_path'].isna().sum()
print(f"Need to fetch posters for {remaining_work} movies")

if remaining_work == 0:
    print("All movies already have posters! Nothing to do.")
    exit()

success_count = 0
fail_count = 0
batch_size = 500
processed_count = 0

print("\nStarting poster fetch process...")
print("=" * 50)

for idx, row in df.iterrows():
    # Skip movies that already have posters
    if pd.notna(row.get("poster_path")):
        continue
        
    tmdb_id = row.get("tmdbId")
    title = row.get("title", "Unknown Title")

    if pd.isna(tmdb_id):
        continue

    processed_count += 1
    url = BASE_URL.format(int(tmdb_id), API_KEY)
    poster_path = None

    for attempt in range(3):  # Increased retry attempts
        try:
            response = requests.get(url, timeout=15)  # Increased timeout
            if response.status_code == 200:
                poster_path = response.json().get("poster_path")
                if poster_path:
                    df.at[idx, "poster_path"] = IMAGE_BASE_URL + poster_path
                    print(f"{processed_count:4d}/{remaining_work} | {title} -> Poster found")
                    success_count += 1
                else:
                    print(f"{processed_count:4d}/{remaining_work} | {title} -> No poster available")
                    fail_count += 1
                break
            elif response.status_code == 429:  # Rate limit
                wait_time = 5 * (attempt + 1)
                print(f"Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"{processed_count:4d}/{remaining_work} | {title} -> API error {response.status_code}")
                if attempt == 2:  # Final attempt
                    fail_count += 1
                    break
                    
        except requests.exceptions.ConnectionError as e:
            wait_time = 3 * (attempt + 1)
            if attempt < 2:
                print(f"Connection error for {title}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"{processed_count:4d}/{remaining_work} | {title} -> Connection failed after retries")
                fail_count += 1
                
        except Exception as e:
            if attempt < 2:
                print(f"Error for {title}: {str(e)[:50]}... Retrying...")
                time.sleep(2)
            else:
                print(f"{processed_count:4d}/{remaining_work} | {title} -> Final error: {str(e)[:50]}...")
                fail_count += 1

    # Increased delay to avoid rate limiting
    time.sleep(1.0)

    # Save progress every batch with error handling
    if processed_count % batch_size == 0:
        try:
            df.to_csv(output_file, index=False)
            completion_pct = (processed_count / remaining_work) * 100
            print(f"Progress saved: {processed_count}/{remaining_work} ({completion_pct:.1f}%)")
        except PermissionError:
            print("Could not save progress - file may be open elsewhere")

# Final save with error handling
try:
    df.to_csv(output_file, index=False)
    print(f"\nFinal dataset saved to {output_file}")
except PermissionError as e:
    print(f"\nPermission error saving final file: {e}")
    # Try saving with timestamp as backup
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"movies_with_posters_backup_{timestamp}.csv"
    df.to_csv(backup_file, index=False)
    print(f"Backup saved as {backup_file}")

# Save failed movies separately
try:
    failed_df = df[df["poster_path"].isna()]
    failed_df.to_csv(failed_file, index=False)
    print(f"Failed movies saved to {failed_file}")
except PermissionError:
    print("Could not save failed movies file")

print("\n" + "=" * 50)
print("POSTER FETCH SUMMARY")
print("=" * 50)
print(f"Total movies in dataset: {len(df)}")
print(f"Movies processed this run: {processed_count}")
print(f"Posters successfully found: {success_count}")
print(f"Movies without posters: {fail_count}")
print(f"Total movies with posters: {df['poster_path'].notna().sum()}")
print(f"Completion rate: {(df['poster_path'].notna().sum() / len(df)) * 100:.1f}%")

if success_count > 0:
    print(f"\nSuccessfully enriched {success_count} movies with poster URLs!")
if fail_count > 0:
    print(f"{fail_count} movies could not be processed (check failed_posters.csv)")

print(f"\nDataset location: {output_file}")

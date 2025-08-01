#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

# DO NOT MODIFY
def go(args):
    """
    Perform basic data cleaning and log the cleaned dataset as a W&B artifact.

    Parameters
    ----------
    args : argparse.Namespace
        input_artifact (str): Name of the raw dataset artifact to download.
        output_artifact (str): Name of the cleaned dataset artifact to upload.
        output_type (str): Type label for the output artifact.
        output_description (str): Description of the output artifact.
        min_price (float): Minimum valid price for filtering listings.
        max_price (float): Maximum valid price for filtering listings.
    """
    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    
    run = wandb.init(project="nyc_airbnb", group="cleaning", save_code=True)
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)
    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    #Drop out-of-bounds values
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    # Save the cleaned file
    df.to_csv('clean_sample.csv',index=False)

    # log the new data.
    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
 )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")
  
    parser.add_argument(
        "--input_artifact", 
        type = str,
        help = "Name of the input artifact to be cleaned",
        required = True
    )

    parser.add_argument(
        "--output_artifact", 
        type = str,
        help = "Name for the output cleaned data artifact",
        required = True
    )

    parser.add_argument(
        "--output_type", 
        type = str,
        help = "Type of the output artifact",
        required = True
    )

    parser.add_argument(
        "--output_description", 
        type = str,
        help = "Description of the output artifact",
        required = True
    )

    parser.add_argument(
        "--min_price", 
        type = float,
        help = "Minimum price for a listing",
        required = True
    )

    parser.add_argument(
        "--max_price",
        type = float,
        help = "Maximum price for a listing",
        required = True
    )


    args = parser.parse_args()

    go(args)
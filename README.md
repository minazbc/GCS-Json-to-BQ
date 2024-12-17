# S1-assignment

## Task 
Load JSON files with nested columns uploaded to Cloud Storage, based on provided mapping structure, into BigQuery table. Files can be as large as millions of rows.

## Implementation & Solution

My standard approach to implementing new data pipeline is to review most suitable tools for the task at hand. In this case, although not having personally worked with it yet, Dataflow (in combination with other GCP tools) proved to be one of the most optimal solutions to process large files daily.

See overview of implemented pipeline below.

![s1_assignment (1)](https://github.com/user-attachments/assets/4e20b720-4519-40d4-aed3-dc4d9beb049e)

### Step 0: Terraform (IaC) Infrastructure Creation

Terraform code creates following infrastructure using ```terraform apply```:
* **BigQuery**: dataset, table,
* **Cloud Storage Buckets & Files** (Buckets): _Files_, _Archive_, _Temp_, _Assets_ (incl. Dataflow Template and Cloud functions source code upload),
* **Pub/Sub Topic & Subscription**,
* **Cloud Functions** from .zip,
* **Dataflow Pipeline** from template.

Note that some Terraform-related files (such as auth or variables) are ignored in .gitignore for security reasons.

### Step 1: Dataflow with Daily Schedule to Process Large Files

Based on my initial investigation, Dataflow proved to be one of the best GCP tools for processing large files efficiently. It offers scalable approach in its resources and is easily integrated with other GCP services.

To process large JSON files uploaded daily, I decided to set scheduled daily BATCH pipeline.

**Reasoning**: The assumption is, especially in case of large files resulting in lots of inserted data, the resulting data model most likely runs on scheduled times (1-2 times a day) rather than reprocessing data all the time. Therefore it's better to align the data pipeline with the model schedule and there is no need to keep the pipeline in streaming mode, processing files immediately.

**Dataflow pipeline steps**

1. Read all existing JSON files in bucket.
2. Transform, map and filter data based on required schema.
3. Upload the data to destination BigQuery table.
4. Get status of BigQuery inserting job from previous step (3). Wait until the jobs are done (max. 10 retries until failure, can be adjusted).
5. Create message for Pub/Sub. This includes job status, source and archive bucket name.
6. Publish message to Pub/Sub to trigger Cloud functions (see Step 2 below).

### Step 2: Archive Files with Triggered Cloud Functions
1. Read the message received from Dataflow pipeline - proceed if BigQuery job was successfully done.
3. Move files from "Files" bucket to "Archive". To each file name, append datetime to assure filenames uniqueness.
4. Confirm no JSON files remain unarchived.
   

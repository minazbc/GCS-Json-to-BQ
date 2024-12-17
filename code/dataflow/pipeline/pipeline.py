import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from pipeline.options import DataflowPipelineOptions
from pipeline import functions as fn 

def run():
      
    options = PipelineOptions().view_as(DataflowPipelineOptions)
    pipeline_options = PipelineOptions(
        runner = "DataflowRunner",
        project = "original-brace-444522-d1",
        region = "europe-west1",
        temp_location = "gs://original-brace-444522-d1_dataflow_temp/temp/",
        staging_location = "gs://original-brace-444522-d1_dataflow_temp/staging/",
        machine_type="n2-standard-2", # 2 CPU, 8 GB RAM
        num_workers=2,
        max_num_workers=15
    )
    
    bq_schema = fn.get_table_schema(f"{options.project_name}.{options.dataset}.{options.table}")

    with beam.Pipeline(options=pipeline_options) as pipeline:
        result = (
            pipeline
            | "Read JSON Files (Source)" >> beam.io.ReadFromText(options.input_bucket + "/*.json")
            | "Parse Data (Transform)" >> beam.Map(fn.parse_data)
            | "Write to BigQuery (Sink)" >> beam.io.WriteToBigQuery(
                method=beam.io.WriteToBigQuery.Method.FILE_LOADS,
                table=options.table,
                dataset=options.dataset,
                schema=bq_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )
        
        _ = (result.destination_load_jobid_pairs
            | "Check Upload Status" >> beam.Map(fn.confirm_data_upload)
            | "Create PubSub Message" >> beam.Map(lambda upload_status: 
                                                   fn.create_archive_pubsub_message(upload_status, options.input_bucket, options.archive_bucket))
            | "Notify PubSub" >> beam.Map(fn.notify_pubsub, topic=options.pubsub_topic)
            )

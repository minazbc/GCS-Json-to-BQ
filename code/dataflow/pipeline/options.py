import json
from apache_beam.options.pipeline_options import PipelineOptions

class DataflowPipelineOptions(PipelineOptions):
    
    @classmethod
    def _add_argparse_args(cls, parser):
        
        parser.add_argument("--project_name", default="original-brace-444522-d1")
        parser.add_argument("--dataset", default="dataflow_assignment")
        parser.add_argument("--table", default="dataflow_data")
        parser.add_argument("--input_bucket", default="gs://original-brace-444522-d1_dataflow_files")
        parser.add_argument("--archive_bucket", default="gs://original-brace-444522-d1_dataflow_archive")
        parser.add_argument("--temp_bucket", default="gs://original-brace-444522-d1_dataflow_temp")
        parser.add_argument("--pubsub_topic", default="projects/original-brace-444522-d1/topics/dataflow-pipeline-done")

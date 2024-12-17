"""
python main.py \
  --setup_file ./setup.py \
  --runner DataflowRunner \
  --project original-brace-444522-d1 \
  --region europe-west1 \
  --temp_location gs://original-brace-444522-d1_dataflow_temp/ \
  --template_location gs://original-brace-444522-d1_assets/templates/dataflow_classic_template.json \
  --save_main_session
"""

from pipeline import pipeline

if __name__ == "__main__":
    pipeline.run()

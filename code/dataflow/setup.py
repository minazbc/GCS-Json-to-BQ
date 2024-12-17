from setuptools import setup, find_packages

setup(
    name="dataflow-pipeline",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "apache-beam[gcp]",
        "google-cloud-bigquery",
        "google-cloud-storage"
    ]
)
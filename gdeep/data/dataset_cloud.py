from ._data_cloud import _DataCloud

import json
import os
from os import remove
from os.path import join, exists
from typing import List, Tuple, Union

import wget  # type: ignore

class DatasetCloud():
    """DatasetCloud class to handle the download and upload
    of datasets to the DataCloud.
    If the download_directory does not exist, it will be created and
    if a folder with the same name as the dataset exists in the
    download directory, it will not be downloaded again.
    If a folder with the same name as the dataset does not exists
    locally, it will be created when downloading the dataset.

    Args:
        dataset_name (str): Name of the dataset to be downloaded or uploaded.
        bucket_name (str, optional): Name of the bucket in the DataCloud.
        Defaults to "adversarial_attack".
        download_directory (Union[None, str], optional): Directory where the
        dataset will be downloaded to. Defaults to None.
        use_public_access (bool, optional): If True, the dataset will
            downloaded via public url. Defaults to False.
        path_credentials (Union[None, str], optional): Path to the credentials
            file.
            Only used if public_access is False and credentials are not
            provided. Defaults to None.
        make_public (bool, optional): If True, the dataset will be made public
        """
    def __init__(self,
             dataset_name: str,
             bucket_name: str = "adversarial_attack",
             download_directory: Union[None, str] = None,
             use_public_access: bool = True,
             path_to_credentials: Union[None, str] = None,
             make_public: bool = True,
             ):
        # Non-public datasets start with "private_"
        if make_public or use_public_access:
            self.name = dataset_name
        else:
            self.name = "private_" + dataset_name
        self.path_metadata = None
        self.use_public_access = use_public_access
        if download_directory is None:
            self.download_directory = join('examples', 'data', 'DataCloud')
        else:
            self.download_directory = download_directory
        
        # Don't create the bucket if using public access.
        if not use_public_access:
            self._data_cloud = _DataCloud(
                bucket_name=bucket_name,
                download_directory = self.download_directory,
                path_to_credentials = path_to_credentials)
        else:
            self.public_url = ("https://storage.googleapis.com/"
                               + bucket_name + "/")
        self.make_public = make_public
        
    def __del__(self):
        """This function deletes the metadata file if it exists.

        Returns:
            None
        """
        if not self.path_metadata == None:
            remove(self.path_metadata)
            
    def download(self):
        """Download a dataset from the DataCloud.

        Raises:
            ValueError: Dataset does not exits in cloud.
        """
        if self.use_public_access:
            self._download_using_url()
        else:
            self._download_using_api()
        
    def _download_using_api(self):
        """Downloads the dataset using the DataCloud API.
        If the dataset does not exist in the bucket, an exception will
        be raised. If the dataset exists locally in the download directory,
        the dataset will not be downloaded again.
        """
        self._check_public_access()
        # List of existing datasets in the cloud.
        existing_datasets = set([blob.name.split('/')[0]
                                 for blob in
                                 self._data_cloud.bucket.list_blobs()\
            if blob.name != "giotto-deep-big.png"])
        if not self.name in existing_datasets:
            raise ValueError("Dataset {} does not exist in the cloud."\
                .format(self.name) +
                             "Available datasets are: {}."\
                                 .format(existing_datasets))
        if self._check_dataset_exists_locally():
            print("Dataset {} already exists".format(self.name) +
                  "in the download directory.")
        else:
            self._create_dataset_folder()
        self._data_cloud.download_folder(self.name + '/')
    
    def _check_dataset_exists_locally(self) -> bool:
        """Check if the dataset exists locally.

        Returns:
            bool: True if the dataset exists locally, False otherwise.
        """
        return exists(join(self.download_directory, self.name))
    
    def _create_dataset_folder(self):
        """Creates a folder with the dataset name in the download directory.
        """
        if not exists(join(self.download_directory, self.name)):
            os.makedirs(join(self.download_directory, self.name))
    
    def _download_using_url(self):
        # List of existing datasets in the cloud.
        existing_datasets = self.get_existing_dataset()
        
        # Check if requested dataset exists in the cloud.
        assert self.name in existing_datasets,\
            ("Dataset {} does not exist in the cloud.".format(self.name) +
             "Available datasets are: {}.".format(existing_datasets))
        
        # Check if dataset exists locally
        if self._check_dataset_exists_locally():
            print("Dataset {} already exists".format(self.name) +
                  "in the download directory.")
        else:
            self._create_dataset_folder()
                    
        # Download the dataset (metadata.json, data.pt, labels.pt) 
        # by using the public URL.
        wget.download(self.public_url + self.name + "/metadata.json",
                    join(self.download_directory, self.name, 'metadata.json'))
        wget.download(self.public_url + self.name + "/data.pt",
                    join(self.download_directory, self.name, "data.pt"))
        wget.download(self.public_url + self.name + "/labels.pt",
                    join(self.download_directory, self.name, "labels.pt"))
        
    def get_existing_dataset(self) -> List[str]:
        """Returns a list of datasets in the cloud.

        Returns:
            List[str]: List of datasets in the cloud.
        """
        if self.use_public_access:
            datasets_local = "tmp_datasets.json"
            # Download the dataset list json file using the public URL.
            wget.download(self.public_url + 'datasets.json', datasets_local)
            datasets = json.load(open(datasets_local))
            
            # Remove duplicates. This has to be fixed in the future.
            datasets = list(set(datasets))
            
            # Remove the temporary file.
            remove(datasets_local)
            
            return datasets
        else:
            existing_datasets = [blob.name.split('/')[0] 
                    for blob in self._data_cloud.bucket.list_blobs()
                    if blob.name != "giotto-deep-big.png" and
                    blob.name != "datasets.json"]
            # Remove duplicates.
            existing_datasets = list(set(existing_datasets))
            
            # Remove dataset that are not public, i.e. start with "private_".
            existing_datasets = [dataset for dataset in existing_datasets
                                    if not dataset.startswith("private_")]
            
            return existing_datasets

    def _update_dataset_list(self):
        """Updates the dataset list in the datasets.json file.
        """
        self._check_public_access()
        
        # List of existing datasets in the cloud.
        existing_datasets = self.get_existing_dataset()
        
        # Save existing datasets to a json file.
        json_file = 'tmp_datasets.json'
        json.dump(existing_datasets, open(json_file, 'w'))
        
        # Upload the json file to the cloud.
        self._data_cloud.upload_file(json_file,
                                     'datasets.json',
                                     make_public=True,
                                     overwrite=True,
                                     )
        
        # Remove the temporary file.
        remove(json_file)
        
        
        

    @staticmethod
    def _get_filetype(path: str) -> str:
        """Returns the file extension from a given path.
    
        Args:
            path: A string path.
        
        Returns:
            The file extension from the given path.
        
        Raises:
            None.
        """
        return path.split('.')[-1]
    
    def _check_public_access(self) -> None:
        """Check if use_public_access is set to False.
        """
        assert self.use_public_access is False,\
            "Only download functionality is supported for public access."
    
    def _upload_data(self,
                path: str,) -> None:
        """Uploads the data file to a Cloud Storage bucket.

        Args:
        path: The path to the data file.

        Raises:
        ValueError: If the file type is not supported."""
        self._check_public_access()
        
        filetype = DatasetCloud._get_filetype(path)
        assert filetype in ('pt', 'npy'), "File type not supported."
        self._data_cloud.upload_file(path, str(self.metadata['name'])
                                     + '/data.' + filetype,
                                     make_public=self.make_public,)
    
    def _upload_label(self,
                 path: str,) -> None:
        """Uploads a set of labels to a remote dataset.

        Args:
            path: the path to the labels file.

        Returns:
            None

        Raises:
            AssertionError: if the path is not valid or the filetype is not 
            supported.
        """
        filetype = DatasetCloud._get_filetype(path)
        assert filetype in ('pt', 'npy'), "File type not supported."
        self._data_cloud.upload_file(path, str(self.metadata['name']) 
                                     +'/labels.' + filetype,
                                     make_public=self.make_public,)
    
    def _upload_metadata(self,
                        path: Union[str, None]=None):
        """Uploads the metadata dictionary to the location specified in the
        metadata. The metadata dictionary is generated using create_metadata.
        
        Args:
            path (str): The path to the data cloud folder. If none, path will
            be set to the default path.
            
        Raises:
            Exception: If no metadata exists, an exception will be raised."""
        self._check_public_access()
        if self.metadata == None:
            raise Exception("No metadata to upload. " #NOSONAR
                            + "Please create metadata using create_metadata.")
        self._data_cloud.upload_file(
            path, str(self.metadata['name']) + '/'  # type: ignore
            + 'metadata.json',
            make_public=self.make_public)
        
    def _add_metadata(self,
                     size_dataset: int,
                     input_size: Tuple[int, ...],
                     num_labels: Union[None, int] = None,
                     data_type: str = "tabular",
                     task_type: str = "classification",
                     name: Union[None, str]=None,
                     data_format: Union[None, str]=None,
                     comment: Union[None, str]=None,
                     ):
        """This function accepts various metadata for the dataset and stores it 
        in a temporary JSON file.

        Args:
            size_dataset (int): The size of the dataset (in terms of the number
            of samples).
            input_size (Tuple[int, ...]): The size of each sample in the 
            dataset.
            num_labels (Union[None, int]): The number of classes in the dataset.
            data_type (str): The type of data in the dataset.
            task_type (str): The task type of the dataset.
            name (Union[None, str]): The name of the dataset.
            data_format (Union[None, str]): The format of the data in the
            dataset.
            comment (Union[None, str]): A comment describing the dataset.

        Returns:
            None
        """
        self._check_public_access()
        if name is None:
            name = self.name
        if data_format is None:
            data_format = "pytorch_tensor"
        self.path_metadata = "tmp_metadata.json"  # type: ignore
        self.metadata = {'name': name,
                    'size': size_dataset,
                    'input_size': input_size,
                    'num_labels': num_labels,
                    'task_type': task_type,
                    'data_type': data_type,
                    'data_format': data_format,
                    'comment': comment
                    }
        with open(self.path_metadata, "w") as f:  # type: ignore
            json.dump(self.metadata, f, sort_keys=True, indent=4)
        
    def _upload(self,
                       path_data: str,
                       path_label: str,
                       path_metadata: Union[str, None] = None,
                       ):
        """Uploads a dataset to the cloud.

        Args:
            path_data (str): Path to the data files.
            path_label (str): Path to the label file.
            path_metadata (Optional[str]): Path to the metadata file.

        Raises:
            ValueError: If the dataset already exists in the cloud."""
        self._check_public_access()
        
        # List of existing datasets in the cloud.
        existing_datasets = set([blob.name.split('/')[0]
                            for blob in self._data_cloud.bucket.list_blobs()\
                            if blob.name != "giotto-deep-big.png"])
        if self.name in existing_datasets:
            raise ValueError("Dataset {} already exists in the cloud."\
                .format(self.name) +
                "Available datasets are: {}.".format(existing_datasets))
        if path_metadata is None:
            path_metadata = self.path_metadata
        self._upload_metadata(path_metadata)
        self._upload_data(path_data)
        self._upload_label(path_label)
        
        # Update dataset list.
        self._update_dataset_list()
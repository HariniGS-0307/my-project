{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "83f1ff9f",
   "metadata": {
    "_cell_guid": "349c111d-8a62-48a9-b36e-43024d08f9f1",
    "_uuid": "65fa8981-5ee8-48b4-9926-7ee34542bb12",
    "collapsed": false,
    "execution": {
     "iopub.execute_input": "2025-09-17T16:01:28.007246Z",
     "iopub.status.busy": "2025-09-17T16:01:28.006826Z",
     "iopub.status.idle": "2025-09-17T16:01:28.162841Z",
     "shell.execute_reply": "2025-09-17T16:01:28.161674Z"
    },
    "jupyter": {
     "outputs_hidden": false
    },
    "papermill": {
     "duration": 0.162354,
     "end_time": "2025-09-17T16:01:28.165676",
     "exception": false,
     "start_time": "2025-09-17T16:01:28.003322",
     "status": "completed"
    },
    "tags": []
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Error connecting to database: connection to server at \"localhost\" (127.0.0.1), port 5432 failed: Connection refused\n",
      "\tIs the server running on that host and accepting TCP/IP connections?\n",
      "connection to server at \"localhost\" (::1), port 5432 failed: Cannot assign requested address\n",
      "\tIs the server running on that host and accepting TCP/IP connections?\n",
      "\n"
     ]
    }
   ],
   "source": [
    "import psycopg2\r\n",
    "\r\n",
    "try:\r\n",
    "    # Connect to your database\r\n",
    "    conn = psycopg2.connect(\r\n",
    "        host=\"localhost\",\r\n",
    "        database=\"mydb\",\r\n",
    "        user=\"postgres\",\r\n",
    "        password=\"yourpassword\"  # replace with your PostgreSQL password\r\n",
    "    )\r\n",
    "    \r\n",
    "    # Create a cursor object\r\n",
    "    cur = conn.cursor()\r\n",
    "    \r\n",
    "    print(\"Connection successful!\")\r\n",
    "\r\n",
    "except Exception as e:\r\n",
    "    print(\"Error connecting to database:\", e)"
   ]
  }
 ],
 "metadata": {
  "kaggle": {
   "accelerator": "none",
   "dataSources": [],
   "dockerImageVersionId": 31089,
   "isGpuEnabled": false,
   "isInternetEnabled": true,
   "language": "python",
   "sourceType": "notebook"
  },
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.13"
  },
  "papermill": {
   "default_parameters": {},
   "duration": 7.21451,
   "end_time": "2025-09-17T16:01:28.688843",
   "environment_variables": {},
   "exception": null,
   "input_path": "__notebook__.ipynb",
   "output_path": "__notebook__.ipynb",
   "parameters": {},
   "start_time": "2025-09-17T16:01:21.474333",
   "version": "2.6.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}

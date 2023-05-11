# Рубрикатор клинических рекомендаций
The directory contains the results of data collection from [Рубрикатор клинических рекомендаций](https://cr.minzdrav.gov.ru/clin_recomend).

## Structure
This directory has the following structure:
| Name | Description |
| --- | --- |
| `collect_pages_id.py` | program code in Python 3.10 for collecting page IDs with clinical guidelines |
| `main.py` | program code in Python 3.10 for collecting data from each clinical guidelines |
| `requirements.txt` | file listing all the dependencies |
| `data/identifications.txt` | file with set of pages ID with clinical recommendations, the result of the code `collect_pages_id.py` | 
| `data/minzdrav.zip` | collected data of the information resource, the archive of the result of the code `main.py` |

# ml-pharm: Data Collection - Medscape
[Medscape](https://reference.medscape.com/drugs) is a website providing access to medical information for clinicians and medical scientists; the organization also provides continuing education for physicians and health professionals.

The program is developed in Python 3.10

## Structure
This directory has the following structure:
| Name | Description |
| --- | --- |
| `collect_links.py` | program code in Python 3.10 for collecting URL pages |
| `main.py` | program code in Python 3.10 for collecting data |
| `requirements.txt` | file listing all the dependencies |
| `data/links.txt` | file with set of URLs for collecting data |
| `data/medscape_en.zip` | collected data of the information resource, the archive of the result of the code `main.py` |
| `data/medscape_ru.zip` | translated collected data, the source is the archive `data/medscape_en.zip` |

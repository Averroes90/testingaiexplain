from aixplain.enums import DataType, Language, License, StorageType
from aixplain.factories import CorpusFactory
from aixplain.modules import MetaData

# One MetaData object per CSV column you want to register
id_meta = MetaData(
    name="id",  # Must match the column name in your CSV
    dtype=DataType.TEXT,
    storage_type=StorageType.TEXT,
    languages=[Language.English_UNITED_STATES],
)

content_meta = MetaData(
    name="content",  # Must match the 'content' column from your CSV
    dtype=DataType.TEXT,
    storage_type=StorageType.TEXT,
    languages=[Language.English_UNITED_STATES],
)

doc_type_meta = MetaData(
    name="doc_type",  # Matches the 'doc_type' column in your CSV
    dtype=DataType.TEXT,
    storage_type=StorageType.TEXT,
    languages=[Language.English_UNITED_STATES],
)

created_date_meta = MetaData(
    name="created_date",  # Matches the 'created_date' column
    dtype=DataType.TEXT,  # Dates can be stored as TEXT if there’s no date type
    storage_type=StorageType.TEXT,
    languages=[Language.English_UNITED_STATES],
)

# Combine them into a list
schema = [id_meta, content_meta, doc_type_meta, created_date_meta]

# Then, you'd pass this `schema` alongside your CSV to the SDK,
# similar to how the audio example does it, but specifying DataType.TEXT.

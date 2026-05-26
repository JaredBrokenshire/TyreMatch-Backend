from datetime import datetime
from database.session import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime


class TyreImpressionProcessing(Base):
    __tablename__ = 'tyre_impression_processing'

    id = Column(Integer, primary_key=True)
    tyre_impression_id = Column(
        Integer,
        ForeignKey('tyre_impressions.id'),
        nullable=False,
        unique=True
    )

    normalised_path = Column(String(255), nullable=True)
    enhanced_path = Column(String(255), nullable=True)
    binary_path = Column(String(255), nullable=True)
    clean_path = Column(String(255), nullable=True)
    skeleton_path = Column(String(255), nullable=True)

    edge_density = Column(Float, nullable=True)
    void_ratio = Column(Float, nullable=True)
    groove_count = Column(Integer, nullable=True)

    feature_vector_json = Column(LONGTEXT, nullable=True)
    match_results_json = Column(LONGTEXT, nullable=True)

    pipeline_version = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime, nullable=True, default=datetime.now)

    # Define relationships
    tyre_impression = relationship(
        "TyreImpression",
        uselist=False,
        single_parent=True,
    )

    def __repr__(self):
        return f"<TyreImpressionProcessing {self.id} v{self.pipeline_version}>"
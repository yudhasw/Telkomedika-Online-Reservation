import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from models.reservasi import Reservasi

@pytest.fixture
def mock_db_session():
    mock_db = MagicMock()
  
    with patch('models.reservasi.db', mock_db):
        yield mock_db.session

class TestReservasiCreateWhiteBox:

    def test_create_success_path(self, mock_db_session):
        data_input = {
            "pasien_id": 13,
            "jadwal_id": "a8c99333-a8f6-4574-9fdf-d0e403fc8610",
            "no_urut": 1,
            "tanggal": date(2025, 12, 14),
            "status": "Menunggu",
            "is_reminded": 0
        }

        reservasi, error = Reservasi.create(**data_input)

        assert error is None
        assert reservasi is not None
        assert reservasi.no_urut == 1
    
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()
        
        print("\n[SUCCESS] Path 1 Tested: Database Transaction Success")

    def test_create_failure_path_db_error(self, mock_db_session):
        data_input = {
            "pasien_id": 13,
            "jadwal_id": "a8c99333-a8f6-4574-9fdf-d0e403fc8610",
            "no_urut": 1,
            "tanggal": date(2025, 12, 14),
            "status": "Menunggu",
            "is_reminded": 0
        }
  
        mock_db_session.commit.side_effect = SQLAlchemyError("Simulasi Database Error")

        reservasi, error = Reservasi.create(**data_input)

        assert reservasi is None
        assert "Simulasi Database Error" in error
   
        mock_db_session.add.assert_called_once() 
   
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_called_once() 
        
        print("\n[SUCCESS] Path 2 Tested: Database Transaction Failure (Rollback)")
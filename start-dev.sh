#!/bin/bash

echo "========================================"
echo " Fake News Detection System"
echo " Starting Development Environment"
echo "========================================"
echo ""

echo "Checking if MongoDB is running..."
if pgrep -x "mongod" > /dev/null
then
    echo "[OK] MongoDB is running"
else
    echo "[WARNING] MongoDB is not running!"
    echo "Please start MongoDB first:"
    echo "  - Run: sudo systemctl start mongod"
    echo "  - Or use MongoDB Atlas cloud database"
    echo ""
    read -p "Press any key to continue anyway..."
fi

echo ""
echo "Starting all services..."
echo "- Frontend: http://localhost:3000"
echo "- Backend: http://localhost:5000"
echo "- AI API: http://localhost:5001"
echo ""

npm run dev

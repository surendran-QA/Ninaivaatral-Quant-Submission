@echo off
echo =======================================================
echo          WIPING COGNEE BRAIN (GRAPH DATABASE)
echo =======================================================
echo.
echo WARNING: This will delete all saved nodes, edges, and past memory!
pause

echo.
echo Deleting IngestionQueue...
rmdir /s /q IngestionQueue 2>nul

echo Deleting FailedPayloads...
rmdir /s /q FailedPayloads 2>nul

echo Deleting .cognee_system (From Strategy Folder)...
rmdir /s /q "C:\Surendran\Statergy devolpment\FVP_IB_Strategy\CONGEE\.cognee_system" 2>nul

echo Deleting .cognee_data (From Strategy Folder)...
rmdir /s /q "C:\Surendran\Statergy devolpment\FVP_IB_Strategy\CONGEE\.cognee_data" 2>nul

echo.
echo BRAIN SUCCESSFULLY WIPED! 
echo You are ready to start a completely fresh Market Replay session.
echo.
pause

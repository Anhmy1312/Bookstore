# reset_db.ps1 — Dua CSDL nha_sach ve dung du lieu mau trong schema.sql
# Dung:  .\reset_db.cmd            (co sao luu truoc khi reset)
#        .\reset_db.cmd -NoBackup   (khong sao luu)
# Hoac:  powershell -NoProfile -ExecutionPolicy Bypass -File .\reset_db.ps1

param([switch]$NoBackup)

$ErrorActionPreference = "Stop"
try { chcp 65001 | Out-Null } catch {}
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path ".env")) { throw "Khong thay file .env trong $root" }
if (-not (Test-Path "schema.sql")) { throw "Khong thay schema.sql trong $root" }

$mysql = "C:\Program Files\MySQL\MySQL Server 26.7\bin\mysql.exe"
$dumpExe = "C:\Program Files\MySQL\MySQL Server 26.7\bin\mysqldump.exe"
if (-not (Test-Path $mysql)) {
    $found = Get-Command mysql.exe -ErrorAction SilentlyContinue
    if ($found) { $mysql = $found.Source } else { throw "Khong tim thay mysql.exe (kiem tra MySQL da cai chua)" }
}

$user = ((Get-Content .env | Where-Object { $_ -match '^DB_USER=' }) -replace '^DB_USER=', '')
$pass = ((Get-Content .env | Where-Object { $_ -match '^DB_PASSWORD=' }) -replace '^DB_PASSWORD=', '')
if (-not $user) { $user = "root" }
$env:MYSQL_PWD = $pass

try {
    Write-Host "== TRUOC KHI RESET ==" -ForegroundColor Cyan
    & $mysql -u $user --default-character-set=utf8mb4 -e "USE nha_sach; SELECT (SELECT COUNT(*) FROM sach) AS sach, (SELECT COUNT(*) FROM phieu_nhap) AS phieu_nhap, (SELECT COUNT(*) FROM don_hang) AS don_hang;"

    if (-not $NoBackup) {
        $dir = Join-Path $env:LOCALAPPDATA "Temp\opencode\nha_sach_reset"
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        $file = Join-Path $dir ("backup_nha_sach_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".sql")
        $eap = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $dumpExe -u $user --default-character-set=utf8mb4 --set-gtid-purged=OFF "--result-file=$file" --databases nha_sach 2>&1 | Out-Null
        $dumpCode = $LASTEXITCODE
        $ErrorActionPreference = $eap
        if ($dumpCode -ne 0) { throw "Sao luu that bai (exit $dumpCode)" }
        Write-Host ("Da sao luu: " + $file + " (" + (Get-Item $file).Length + " bytes)") -ForegroundColor DarkGray
    }

    Write-Host "== DANG CHAY schema.sql ==" -ForegroundColor Yellow
    cmd /c ('"' + $mysql + '" -u ' + $user + ' --default-character-set=utf8mb4 < schema.sql')
    if ($LASTEXITCODE -ne 0) { throw "Chay schema.sql that bai (exit $LASTEXITCODE)" }

    Write-Host "== SAU KHI RESET ==" -ForegroundColor Green
    & $mysql -u $user --default-character-set=utf8mb4 -e "USE nha_sach; SELECT (SELECT COUNT(*) FROM nguoi_dung) AS nguoi_dung, (SELECT COUNT(*) FROM quy_dinh) AS quy_dinh, (SELECT COUNT(*) FROM the_loai) AS the_loai, (SELECT COUNT(*) FROM sach) AS sach, (SELECT COUNT(*) FROM phieu_nhap) AS phieu_nhap, (SELECT COUNT(*) FROM chi_tiet_phieu_nhap) AS ct_phieu_nhap, (SELECT COUNT(*) FROM don_hang) AS don_hang, (SELECT COUNT(*) FROM chi_tiet_don_hang) AS ct_don_hang;"
    & $mysql -u $user --default-character-set=utf8mb4 -e "USE nha_sach; SELECT ten, gia_tri FROM quy_dinh ORDER BY ten;"

    Write-Host "Xong. Du lieu mau: 5 nguoi_dung / 3 quy_dinh / 5 the_loai / 20 sach, cac bang giao dich = 0." -ForegroundColor Green
    Write-Host "Mat khau cac tai khoan mau: 123456" -ForegroundColor Green
}
finally {
    Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue
}

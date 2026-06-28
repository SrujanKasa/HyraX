$root = 'C:\Users\ASUS\OneDrive\Documents\Projects\HyraX\dashboard'
$port = 5502
$mime = @{
    '.html' = 'text/html; charset=utf-8'
    '.js'   = 'application/javascript'
    '.css'  = 'text/css'
    '.mp4'  = 'video/mp4'
    '.png'  = 'image/png'
    '.ico'  = 'image/x-icon'
    '.json' = 'application/json'
}

$http = [System.Net.HttpListener]::new()
$http.Prefixes.Add("http://localhost:$port/")
$http.Start()
Write-Host "HyraX server → http://localhost:$port" -ForegroundColor Cyan

$handleScript = {
    param($ctx, $root, $mime)
    try {
        $req  = $ctx.Request
        $res  = $ctx.Response
        $path = $req.Url.LocalPath
        if ($path -eq '/' -or $path -eq '') { $path = '/index.html' }
        $file = Join-Path $root ($path.TrimStart('/').Replace('/', '\'))
        $ext  = [System.IO.Path]::GetExtension($file).ToLower()
        $ct   = if ($mime[$ext]) { $mime[$ext] } else { 'application/octet-stream' }

        if (-not (Test-Path $file -PathType Leaf)) {
            $res.StatusCode = 404; $res.Close(); return
        }

        $fileLen  = (Get-Item $file).Length
        $rangeHdr = $req.Headers['Range']

        if ($rangeHdr -and $ct -eq 'video/mp4') {
            # Parse "bytes=start-end"
            $range = $rangeHdr -replace 'bytes=', ''
            $parts = $range -split '-'
            $start = [long]$parts[0]
            $end   = if ($parts[1] -ne '') { [long]$parts[1] } else { [Math]::Min($start + 1048576, $fileLen - 1) }
            $chunkLen = $end - $start + 1

            $res.StatusCode = 206
            $res.ContentType = $ct
            $res.ContentLength64 = $chunkLen
            $res.Headers.Add('Content-Range', "bytes $start-$end/$fileLen")
            $res.Headers.Add('Accept-Ranges', 'bytes')

            $fs     = [System.IO.FileStream]::new($file, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
            $fs.Seek($start, [System.IO.SeekOrigin]::Begin) | Out-Null
            $buf    = New-Object byte[] $chunkLen
            $read   = $fs.Read($buf, 0, $chunkLen)
            $fs.Close()
            $res.OutputStream.Write($buf, 0, $read)
        } else {
            $bytes = [System.IO.File]::ReadAllBytes($file)
            $res.ContentType     = $ct
            $res.ContentLength64 = $bytes.Length
            $res.Headers.Add('Accept-Ranges', 'bytes')
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
        }
    } catch {}
    finally { try { $ctx.Response.Close() } catch {} }
}

$pool = [System.Management.Automation.Runspaces.RunspaceFactory]::CreateRunspacePool(1, 20)
$pool.Open()

while ($http.IsListening) {
    $ctx = $http.GetContext()
    $ps  = [PowerShell]::Create()
    $ps.RunspacePool = $pool
    [void]$ps.AddScript($handleScript).AddArgument($ctx).AddArgument($root).AddArgument($mime)
    [void]$ps.BeginInvoke()
}

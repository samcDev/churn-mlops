$ErrorActionPreference = 'Stop'
function K { & kubectl @args; if ($LASTEXITCODE -ne 0) { throw "kubectl failed: $args" } }
New-Item -ItemType Directory -Force evidence | Out-Null
Start-Transcript -Path evidence/kubernetes-transcript.txt -Force
try {
  $ctx = kubectl config current-context
  if ($ctx -ne 'docker-desktop') { throw 'Select Docker Desktop context first.' }
  K -n churn rollout status deployment/churn-api --timeout=300s
  K -n churn get pods -o wide
  python scripts/balance.py --min-pods 3
  if ($LASTEXITCODE -ne 0) { throw 'Balance verification failed' }
  Copy-Item evidence/balance.json evidence/balance-three.json
  $before = (kubectl -n churn get pods -l app=churn-api -o json | ConvertFrom-Json).items
  $old = $before[0]
  K -n churn delete pod $old.metadata.name --wait=true
  $deadline = (Get-Date).AddSeconds(180)
  do {
    Start-Sleep -Seconds 2
    $after = (kubectl -n churn get pods -l app=churn-api -o json | ConvertFrom-Json).items
    $ready = @($after | Where-Object { $_.status.containerStatuses -and $_.status.containerStatuses[0].ready -and -not $_.metadata.deletionTimestamp })
    $new = @($ready | Where-Object { $_.metadata.uid -notin $before.metadata.uid })
  } until (($ready.Count -eq 3 -and $new.Count -ge 1) -or (Get-Date) -gt $deadline)
  if ($ready.Count -ne 3 -or $new.Count -lt 1) { throw 'Replacement Pod was not Ready before deadline' }
  @{old_uid=$old.metadata.uid;old_name=$old.metadata.name;new_pods=$new.metadata;ready_count=$ready.Count} | ConvertTo-Json -Depth 10 | Set-Content evidence/recovery.json
  python scripts/balance.py --min-pods 3
  if ($LASTEXITCODE -ne 0) { throw 'Service failed after replacement' }
  Copy-Item evidence/balance.json evidence/balance-recovered.json
  K -n churn scale deployment/churn-api --replicas=5
  K -n churn rollout status deployment/churn-api --timeout=300s
  $scaled = kubectl -n churn get deployment churn-api -o json | ConvertFrom-Json
  if ($scaled.status.readyReplicas -ne 5) { throw 'Five replicas were not Ready' }
  $scaled | ConvertTo-Json -Depth 30 | Set-Content evidence/scaled-five.json
  python scripts/balance.py --requests 250 --min-pods 5
  if ($LASTEXITCODE -ne 0) { throw 'Five-Pod balance verification failed' }
  Copy-Item evidence/balance.json evidence/balance-five.json
  K -n churn scale deployment/churn-api --replicas=3
  K -n churn rollout status deployment/churn-api --timeout=300s
  K -n churn get endpointslices -l kubernetes.io/service-name=churn-api -o yaml
} finally { Stop-Transcript }

$ErrorActionPreference = 'Stop'
foreach ($case in @('normal','data','concept')) {
  python -m src.drift $case
  $actual = $LASTEXITCODE
  $expected = if ($case -eq 'normal') { 0 } else { 2 }
  "$case exit=$actual expected=$expected" | Tee-Object -FilePath evidence/drift-exit-codes.txt -Append
  if ($actual -ne $expected) { throw "Unexpected drift result for $case" }
}

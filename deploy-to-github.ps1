# 推送到GitHub部署仓库

# 1. 首先在C:\Users\Administrator\.ssh\目录下创建密钥文件
# 文件名: github_fupukeji
# 将下面的私钥内容保存到该文件:
# -----BEGIN OPENSSH PRIVATE KEY-----
# b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
# QyNTUxOQAAACA0j282S6aLR7siUEswGKo4B4uV5+GTaPAKlt2CQx9ByAAAAKBHj5CpR4+Q
# qQAAAAtzc2gtZWQyNTUxOQAAACA0j282S6aLR7siUEswGKo4B4uV5+GTaPAKlt2CQx9ByA
# AAAEBj1gigOuD2vzVojCDgvFMRjhsAi44AHNz9RoOrW4bGDDSPbzZLpotHuyJQSzAYqjgH
# i5Xn4ZNo8AqW3YJDH0HIAAAAGXdhbmd5b25ncWluZ0BmdXB1a2VqaS5jb20BAgME
# -----END OPENSSH PRIVATE KEY-----

# 2. 添加SSH配置
$sshConfigPath = "$env:USERPROFILE\.ssh\config"
$sshConfig = @"
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_fupukeji
    IdentitiesOnly yes
"@

# 检查config文件是否存在
if (Test-Path $sshConfigPath) {
    $existingConfig = Get-Content $sshConfigPath -Raw
    if (-not $existingConfig.Contains("github_fupukeji")) {
        Add-Content $sshConfigPath "`n$sshConfig"
        Write-Host "SSH config已更新"
    }
} else {
    Set-Content $sshConfigPath $sshConfig
    Write-Host "SSH config已创建"
}

# 3. 修改远程仓库为SSH方式
Set-Location "c:\Users\Administrator\Desktop\timevalue"
git remote set-url github git@github.com:fupukeji/allmine.git

# 4. 推送到GitHub
git push github main:master

Write-Host "部署完成！"

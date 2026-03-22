# 博客项目部署与运维指南（面向 Docker 新手）

这份文档按“复制命令就能跑”的思路写，适合第一次接触 Docker 的同学。

适用域名示例：`thousand-tech.com`、`www.thousand-tech.com`  
服务器系统：Ubuntu（22.04/24.04 都可）

---

## 1. 你将得到什么

本项目使用三容器架构：

- `web`：Django + Gunicorn（应用本体）
- `nginx`：反向代理，暴露 80/443
- `certbot_renew`：自动续期 HTTPS 证书（每 12 小时检查一次）

首次签发证书时，额外使用一次 `certbot`（手动命令触发）。

---

## 2. 部署前检查（非常重要）

### 2.1 DNS 解析

在域名控制台添加两条 A 记录（指向你的服务器公网 IP）：

- `thousand-tech.com` -> `你的服务器IP`
- `www.thousand-tech.com` -> `你的服务器IP`

如果你使用 Cloudflare，首次签证书时建议先切到 **DNS only（灰云）**。

### 2.2 放行端口

必须放行：

- `80/tcp`
- `443/tcp`

同时检查云厂商安全组和系统防火墙（UFW）。

---

## 3. 服务器安装 Docker

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

可选：让当前用户免 sudo（重新登录后生效）：

```bash
sudo usermod -aG docker $USER
```

---

## 4. 上传项目并进入目录

假设项目目录是 `/opt/blog`：

```bash
cd /opt/blog
```

确认这里有这些文件：

- `Dockerfile`
- `docker-compose.yml`
- `nginx/start-nginx.sh`
- `nginx/default-http.conf`
- `nginx/default-https.conf`

---

## 5. 配置 Django 生产环境

编辑 `my_blog/.env`（至少修改这几项）：

```env
DEBUG=False
ALLOWED_HOSTS=thousand-tech.com,www.thousand-tech.com
SECRET_KEY=请改成你自己的强随机值
EMAIL_HOST_PASSWORD=你的邮箱授权码
```

---

## 6. 首次启动

```bash
cd /opt/blog
docker compose up -d --build
docker compose ps
```

初始化数据库与静态资源：

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

---

## 7. 首次签发 HTTPS 证书（只需一次）

```bash
cd /opt/blog
docker compose --profile manual run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d thousand-tech.com -d www.thousand-tech.com \
  --email 你的邮箱 \
  --agree-tos --no-eff-email
```

签发后重启 Nginx，让它切换到 HTTPS 配置：

```bash
docker compose restart nginx
```

验证：

```bash
curl -I http://thousand-tech.com
curl -I https://thousand-tech.com
```

---

## 8. 日常运维（常用命令）

### 8.1 查看状态

```bash
docker compose ps
```

### 8.2 查看日志

```bash
docker compose logs --tail=100 web
docker compose logs --tail=100 nginx
docker compose logs --tail=100 certbot_renew
```

### 8.3 更新代码并重启

```bash
cd /opt/blog
git pull
docker compose up -d --build
```

### 8.4 停止/启动

```bash
docker compose down
docker compose up -d
```

---

## 9. 自动续期说明

`certbot_renew` 容器会循环执行：

- `certbot renew --webroot -w /var/www/certbot`
- 每 12 小时检查一次

查看续期日志：

```bash
docker compose logs -f certbot_renew
```

建议每月人工检查一次证书到期时间：

```bash
docker compose --profile manual run --rm certbot certificates
```

---

## 10. 故障排查（最常见）

### 问题 A：申请证书报 `Connection refused`

原因通常是 80 端口不通。  
检查：

1. 云安全组是否放行 80/443
2. 防火墙是否放行 80/443
3. 域名是否指向当前服务器 IP
4. Cloudflare 是否拦截（先灰云）

### 问题 B：Nginx 容器不断重启

先看日志：

```bash
docker compose logs --tail=200 nginx
```

常见原因：

- 脚本换行符错误（Windows CRLF）
- 挂载路径文件/目录类型不匹配
- 证书文件路径写错

### 问题 C：页面能开但静态资源 404

执行：

```bash
docker compose exec web python manage.py collectstatic --noinput
docker compose restart nginx
```

---

## 11. 备份建议（务必做）

至少备份这些内容：

- `my_blog/db.sqlite3`
- `my_blog/media/`
- `certbot-etc` 卷（证书）
- `my_blog/.env`

可先做最简单的文件级备份（按你自己的备份策略扩展）。

---

## 12. 一次性快速检查清单

- [ ] DNS 指向正确 IP
- [ ] 80/443 已放行
- [ ] `.env` 已设 `DEBUG=False`
- [ ] `docker compose ps` 全部 `Up`
- [ ] `https://thousand-tech.com` 可访问
- [ ] `certbot_renew` 日志正常

如果你按本文档执行仍失败，把以下输出发给维护人员：

```bash
docker compose ps
docker compose logs --tail=200 nginx
docker compose logs --tail=200 web
docker compose logs --tail=200 certbot_renew
```


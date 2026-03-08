# blog
个人网站搭建，参考 https://github.com/stacklens/django_blog_tutorial 搭建。

## 使用 Docker 部署到 Ubuntu（可通过域名访问）

### 1. 服务器准备
在 Ubuntu 服务器安装 Docker 与 Docker Compose 插件：

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. 上传代码并配置环境变量
将仓库上传到服务器（例如 `/opt/blog`）：

```bash
cd /opt/blog
cp my_blog/.env.example my_blog/.env
```

编辑 `my_blog/.env`：
- `SECRET_KEY` 改为随机强密钥
- `DEBUG=False`
- `ALLOWED_HOSTS` 改为你的域名（逗号分隔）
- `EMAIL_HOST_PASSWORD`、`ALLOWED_IMEIS`、`REGISTER_KEYS` 按实际填写

### 3. 修改域名配置
编辑 `docker/nginx/blog.conf`：
- 将 `server_name blog.example.com;` 改成你的真实域名

### 4. 启动服务

```bash
cd /opt/blog
sudo docker compose up -d --build
```

首次启动会自动执行：
- `python manage.py migrate`
- `python manage.py collectstatic`

### 5. 域名解析
在你的 DNS 服务商中添加 `A` 记录：
- 主机记录：`@` 或 `www`
- 记录值：你的 Ubuntu 服务器公网 IP

等待 DNS 生效后，访问：
- `http://你的域名`

### 6. 常用运维命令

查看日志：
```bash
sudo docker compose logs -f
```

重启：
```bash
sudo docker compose restart
```

停止：
```bash
sudo docker compose down
```

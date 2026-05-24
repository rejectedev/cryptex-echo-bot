# Deployment Guide

## Requirements
- Docker and Docker Compose v2.x
- 2GB RAM minimum
- 10GB storage space
- Internet connection for market data

## Installation

1. Pull the repository:
```bash
git clone https://github.com/50shades0fGraei/cryptex-echo-bot.git
cd cryptex-echo-bot
```

2. Configure environment:
   - Copy `.env.example` to `.env`
   - Update credentials and settings in `.env`

3. Start the application:
```bash
docker compose up -d
```

4. Access the application:
   - Dashboard: http://localhost:3000
   - API: http://localhost:5050

## Render Deployment (Blueprint)

1. Connect your GitHub repository to [Render](https://render.com).
2. Create a new **Blueprint Instance**.
3. Render will automatically detect the `render.yaml` file.
4. Configure the following Environment Variables in the Render Dashboard for the `backend` service:
   - `WEBULL_EMAIL`: Your Webull account email.
   - `WEBULL_PASSWORD`: Your Webull account password.
   - `WEBULL_TRADE_PIN`: Your 6-digit trade PIN.
5. The frontend and backend will be automatically linked via the `frontend_url` and `NEXT_PUBLIC_API_URL` variables defined in the blueprint.

## Security Configuration
- Use strong passwords
- Enable 2FA where possible
- Keep API keys secure
- Regular system updates

## Monitoring
- Check logs: `docker compose logs -f`
- Monitor system resources
- Review trading activity daily
- Check pearl logs for performance

## Backup
- Volume data in:
  - /app/pearl_log.txt
  - /app/royalty/logs/
- Backup command: `docker run --rm -v cryptex-echo-bot_pearl_logs:/data -v $(pwd):/backup alpine tar czf /backup/pearl_logs.tar.gz /data`

## Troubleshooting
1. Container won't start:
   - Check logs: `docker compose logs`
   - Verify ports 3000 and 5050 are free
   - Check disk space

2. Can't connect to dashboard:
   - Verify containers are running
   - Check network connectivity
   - Confirm firewall settings

3. Trading issues:
   - Verify API credentials
   - Check internet connectivity
   - Review pearl logs

## Support
- GitHub Issues: https://github.com/50shades0fGraei/cryptex-echo-bot/issues
- Documentation: /docs
- Community: TBA
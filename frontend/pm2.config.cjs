module.exports = {
  apps: [{
    name: 'timevalue-frontend',
    script: 'npm',
    args: 'run dev',
    cwd: '/opt/timevalue/frontend',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development'
    }
  }]
};

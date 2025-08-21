(function(){
  function refresh(){
    fetch('/api/users/').then(r=>r.json()).then(data=>{
      const map = new Map(data.users.map(u=>[u.username, u]));
      document.querySelectorAll('[data-username]').forEach(b=>{
        const uname = b.getAttribute('data-username');
        const u = map.get(uname);
        if(!u) return;
        b.textContent = u.online ? 'online' : 'last: ' + u.last_seen;
        b.classList.remove('bg-secondary','online','offline'); b.classList.add(u.online ? 'online' : 'offline','badge');
      });
      const status = document.getElementById('status');
      if(status && window.CHAT){
        const other = map.get(window.CHAT.otherUsername);
        if(other){ status.textContent = other.online ? 'status: online' : ('status: last seen ' + other.last_seen); }
      }
    }).catch(()=>{});
  }
  function heartbeat(){ fetch('/api/heartbeat/').catch(()=>{}); }
  refresh(); heartbeat(); setInterval(refresh, 5000); setInterval(heartbeat, 15000);
})();

import http from 'k6/http'
import {sleep,check} from 'k6'


export let options = {
    duration:'30s',
    vus:20
}

  const payload = JSON.stringify({
    username: 'testuser',
    password: 'testpassword',
  });


  let query = "What is 2 + 2 * 8 /3 + 4"


export default function(){
      const res = http.get(
    `http://localhost:8000/user-query?query=${encodeURIComponent(query)}`
  );

  check(res,{
    "is status 200":(r)=> r.status === 200
  });
  sleep(1);
}
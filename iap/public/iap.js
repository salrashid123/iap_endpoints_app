var id_token = None;

function getIdToken() {
    var cookieUrl= '/getIdToken';
    axios.get(cookieUrl,{withCredentials: true})
    .then(function (response) {
        console.log(response.data);
        id_token = response.data;  
        var base64Url = id_token.split('.')[1];
        var base64 = base64Url.replace('-', '+').replace('_', '/');
        parsed_id_token= JSON.parse(window.atob(base64));
        document.getElementById("disp_idToken").innerHTML = JSON.stringify(parsed_id_token, undefined, 2);
        document.getElementById("getEndpoints").disabled = false;
        document.getElementById("taskid").value = Math.floor(Math.random() * 10001);
    })
    .catch(function (error) {
        alert("Unable to /getIdToken");             
});
    
}

function getEndpoints() {
    console.log("running CRUD operations");
    var baseUrl= 'https://api.endpoints.YOUR_PROJECT.cloud.goog';
    var config = {
        headers: {'X-My-Custom-Header': 'Header-Value',
                  'Authorization': 'Bearer ' + id_token
        }
    };
      var tasktext = document.getElementById("tasktext").value;
      var taskid = parseInt(document.getElementById("taskid").value);

      axios.get(baseUrl + '/todos',config)
          .then(function (response) {

              console.log(JSON.stringify(response.data));
              document.getElementById("list1").innerHTML = JSON.stringify(response.data, undefined, 2);

              axios.post(baseUrl + '/todos', {
                id: taskid,
                task: tasktext
              }, config)
              .then(function (response) {

                console.log(JSON.stringify(response.data));
                document.getElementById("post").innerHTML = JSON.stringify(response.data, undefined, 2);

                axios.get(baseUrl + '/todos/' + taskid, config)
                  .then(function (response) {
                    console.log(JSON.stringify(response.data));
                    document.getElementById("get").innerHTML = JSON.stringify(response.data, undefined, 2);

                    axios.delete(baseUrl + '/todos/' + taskid, config)
                      .then(function (response) {
                        console.log(JSON.stringify(response.statusText));
                        document.getElementById("delete").innerHTML = response.statusText;

                        axios.get(baseUrl + '/todos', config)
                        .then(function (response) {
                          console.log(JSON.stringify(response.data));
                          document.getElementById("list2").innerHTML = JSON.stringify(response.data, undefined, 2);
                        })
                        .catch(function (error) {
                          console.log(error);
                          document.getElementById("list2").innerHTML = "Unable to ListItems()";
                        });                        
                        
                      })
                      .catch(function (error) {
                        console.log(error);
                        document.getElementById("delete").innerHTML = "Unable to DeleteItem()";
                      });
                  })
                  .catch(function (error) {
                    console.log(error);
                    document.getElementById("get").innerHTML = "Unable to GetItem()";
                  });
              })
              .catch(function (error) {
                console.log(error);
                document.getElementById("post").innerHTML = "Unable to InsertItem()";
              });
          })
          .catch(function (error) {
              document.getElementById("list1").innerHTML = "Unable to ListItems()";        
      });
}
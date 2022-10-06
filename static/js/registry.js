$("#modal-create").on("show.bs.modal", function (e) {
  $("#form-create").get(0).reset();
});


$("#modal-run").on("show.bs.modal", function (e) {
  $("#form-run").get(0).reset();
  $("#input-tasklet-name").val(run_row.name);
});


$("#btn-save").click(function() {
  var data = $("#form-create").serializeObject();

  axios.post(api_url, data)
    .then(function (response) {
      // console.log(response);
      $("#table").bootstrapTable("refresh", {});
    })
    .catch(function (error) {
      console.log(error);
    });


  $("#modal-create").modal("hide");
});


$("#btn-run").click(function() {
  var data = $("#form-run").serializeObject();

  axios.put(api_url + "?name=" + data.name + "&stream=" + data.stream + "&cycle=" + data.cycle + "&description=" + data.description + "&worker=" + data.worker + "&kvargs=" + data.kvargs)

  $("#modal-run").modal("hide");
});


function actionsFormatter(value, row, index) {
  return [
    '<a class="task-run mr-3" href="javascript:void(0)" title="Run">',
    '<i class="fa fa-play" style="color: #858796"></i>',
    '</a>',
    '<a class="task-view mr-3" href="' + view_runs_url + '?name=' + row.name + '" title="View">',
    '<i class="fa fa-list" style="color: #858796"></i>',
    '</a>',
    '<a class="task-delete" href="javascript:void(0)" title="Delete">',
    '<i class="fa fa-trash" style="color: #858796"></i>',
    '</a>',
  ].join('')
}




window.actionsEvents = {
  "click .task-run": function (e, value, row, index) {
    run_row = row;
    $("#modal-run").modal("show");
  },
  "click .task-delete": function (e, value, row, index) {
    if (!window.confirm("Delete task " + row.name + "?")) {
      return;
    }
    axios.delete(api_url + "?id=" + row.id)
      .then(function (response) {
        // console.log(response);
        $("#table").bootstrapTable("remove", {
          field: "id",
          values: [row.id]
        });
      })
      .catch(function (error) {
        console.log(error);
      });
  }
}

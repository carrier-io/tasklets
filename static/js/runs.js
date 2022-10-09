$("#modal-stream-create").on("show.bs.modal", function (e) {
  $("#form-stream-create").get(0).reset();
});

$("#modal-cycle-create").on("show.bs.modal", function (e) {
  $("#form-cycle-create").get(0).reset();
});

// $("#modal-view").on("show.bs.modal", function (e) {
//   $("#form-view").get(0).reset();
//   $("#view-type").val(view_row.type);
//   $("#view-title").val(view_row.title);
//   $("#view-description").val(view_row.description);
//   $("#view-severity").val(view_row.severity);
//   $("#view-project").val(view_row.project);
//   $("#view-asset").val(view_row.asset);
// });

$("#btn-stream-save").click(function() {
  var data = $("#form-stream-create").serializeObject();

  axios.post(stream_api_url, data)
    .then(function (response) {
      // console.log(response);
      window.location.reload();
    })
    .catch(function (error) {
      console.log(error);
    });

  $("#modal-stream-create").modal("hide");
});


$("#btn-cycle-save").click(function() {
  var data = $("#form-cycle-create").serializeObject();

  axios.post(cycle_api_url, data)
    .then(function (response) {
      // console.log(response);
      window.location.reload();
    })
    .catch(function (error) {
      console.log(error);
    });

  $("#modal-cycle-create").modal("hide");
});


$("#btn-refresh").click(function() {
  $("#table").bootstrapTable("refresh", {});
});

function actionsFormatter(value, row, index) {
  return [
    '<a class="task-view mr-3" href="' + run_logs_url + '?id=' + row.id + '" title="View">',
    '<i class="fa fa-list" style="color: #858796"></i>',
    '</a>',
    '<a class="task-rerun mr-3" href="javascript:void(0)" title="Re-run">',
    '<i class="fa fa-redo" style="color: #858796"></i>',
    '</a>',
    '<a class="task-delete" href="javascript:void(0)" title="Delete">',
    '<i class="fa fa-trash" style="color: #858796"></i>',
    '</a>',
  ].join('')
}

window.actionsEvents = {
  "click .task-rerun": function (e, value, row, index) {
    if (!window.confirm("Re-run " + row.tasklet_name + "?")) {
      return;
    }
    axios.put(runs_url + "?id=" + row.id)
      .then(function (response) {
        // console.log(response);
        $("#table").bootstrapTable("refresh", {});
      })
      .catch(function (error) {
        console.log(error);
      });
  }
}

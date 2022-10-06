$("#modal-create").on("show.bs.modal", function (e) {
  $("#form-create").get(0).reset();
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


function actionsFormatter(value, row, index) {
  return [
    '<a class="schedule-run mr-3" href="javascript:void(0)" title="Run">',
    '<i class="fa fa-play" style="color: #858796"></i>',
    '</a>',
    '<a class="schedule-enable mr-3" href="javascript:void(0)" title="Enable">',
    '<i class="fa fa-toggle-on" style="color: #858796"></i>',
    '</a>',
    '<a class="schedule-disable mr-3" href="javascript:void(0)" title="Disable">',
    '<i class="fa fa-toggle-off" style="color: #858796"></i>',
    '</a>',
    '<a class="schedule-delete" href="javascript:void(0)" title="Delete">',
    '<i class="fa fa-trash" style="color: #858796"></i>',
    '</a>',
  ].join('')
}


window.actionsEvents = {
  "click .schedule-run": function (e, value, row, index) {
    axios.put(api_url + "?id=" + row.id + "&action=run");
  },
  "click .schedule-enable": function (e, value, row, index) {
    axios.put(api_url + "?id=" + row.id + "&action=enable")
      .then(function (response) {
        // console.log(response);
        $("#table").bootstrapTable("refresh", {});
      })
      .catch(function (error) {
        console.log(error);
      });
  },
  "click .schedule-disable": function (e, value, row, index) {
    axios.put(api_url + "?id=" + row.id + "&action=disable")
      .then(function (response) {
        // console.log(response);
        $("#table").bootstrapTable("refresh", {});
      })
      .catch(function (error) {
        console.log(error);
      });
  },
  "click .schedule-delete": function (e, value, row, index) {
    if (!window.confirm("Delete schedule " + row.description + "?")) {
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

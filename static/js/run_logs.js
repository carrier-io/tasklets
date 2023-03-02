const RunLogsApp = {
    delimiters: ['[[', ']]'],
    props: ['run_websocket_url', 'query_websocket_url', 'logs_ts_now'],
    data() {
        return {
            state: 'idle',
            websocket: undefined,
            connection_retries: 5,
            connection_retry_timeout: 5000,
            logs_pull_end: 0,
            logs_tail_ts: 0,
            logs_query_limit: 1000,
            logs_tail_limit: 10000000000,
            logs: []
        }

    },
    mounted() {
      this.state = 'initializing'
      this.logs_pull_end = this.logs_ts_now
      this.logs_tail_ts = this.logs_ts_now + 1
      this.init_websocket()
    },
    // updated() {
    //     var item = $("#logs-body");
    //     item.scrollTop(item.prop("scrollHeight"));
    // },
    computed: {
        reversedLogs: function () {
            return this.logs.reverse()
        },
        websocket_url: function () {
            return this.run_websocket_url + '&start=' + this.logs_tail_ts.toString()  + '&limit=' + this.logs_tail_limit.toString()
        },
    },
    template: `
        <div class="card card-12 mb-5">
            <div class="card-header">
                <div class="row">
                    <div class="col-2"><h3>Logs ([[ state ]])</h3></div>
                </div>
            </div>
            <div class="card-body card-table">
              <div id="logs-body" class="card-body overflow-auto pt-0 pl-3">
                  <ul class="list-group">
                      <li v-for="line in reversedLogs" class="list-group-item">
                          <div style="word-break: break-all; white-space: pre-wrap;">[[ line ]]</div>
                      </li>
                  </ul>
              </div>
            </div>
        </div>
    `,
    methods: {
        init_websocket() {
            this.state = 'connecting'
            this.websocket = new WebSocket(this.websocket_url)
            this.websocket.onmessage = this.on_websocket_message
            this.websocket.onopen = this.on_websocket_open
            this.websocket.onclose = this.on_websocket_close
            this.websocket.onerror = this.on_websocket_error
        },
        on_websocket_open(message) {
            this.state = 'connected'
        },
        on_websocket_message(message) {
            if (message.type !== 'message') {
                console.warn('Unknown message from socket', message)
                return
            }

            const data = JSON.parse(message.data)
            let current_items = []

            data.streams.forEach(stream_item => {
                stream_item.values.forEach(message_item => {
                    console.log('Message item:')
                    console.log(message_item)
                    current_items.push(message_item)
                    this.logs.push(`${stream_item.stream.level} : ${message_item[1]}`)
                })
            })
        },
        on_websocket_close(message) {
            this.state = 'disconnected'
            let attempt = 1;
            const intrvl = setInterval(() => {
                this.init_websocket()
                if (this.state === 'connected' || attempt > this.connection_retries) clearInterval(intrvl)
                attempt ++
            }, this.connection_retry_timeout)
            // setTimeout(websocket_connect, 1 * 1000);
            //    clearInterval(websocket_connect)
        },
        on_websocket_error(message) {
            this.state = 'error'
            this.websocket.close()
        }

    }
}

vueApp.component('runlogsapp', RunLogsApp)

// $(document).on('vue_init', () => {
//     $('#show_config_btn').on('click', () => {
//         $('#showConfigModal button').attr('disabled', true)
//         $('#showConfigModal button[data-toggle=collapse]').attr('disabled', false)
//         $('#showConfigModal button[data-dismiss=modal]').attr('disabled', false)
//         $('#showConfigModal input').attr('disabled', true)
//         $('#showConfigModal input[type=text]').attr('readonly', true)
//     })
//
//     $('#re_run_test').on('click', reRunTest)
//     $( document ).on( 'updateSummaryEvent', updateSummary);
// })
//
// $("#btn-save").click(function() {
//   var data = $("#form-create").serializeObject();
//
//   axios.post(api_url, data)
//     .then(function (response) {
//       // console.log(response);
//       $("#table").bootstrapTable("refresh", {});
//     })
//     .catch(function (error) {
//       console.log(error);
//     });
//
//
//   $("#modal-create").modal("hide");
// });

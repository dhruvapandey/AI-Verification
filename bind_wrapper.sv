// File: bind_wrapper.sv
// This file contains NO logic, only the connection command.

module bind_wrapper;

  bind router router_assertions check_inst (
    .clk(clk),
    .rst_n(rst_n),
    .count(count)
  );

endmodule

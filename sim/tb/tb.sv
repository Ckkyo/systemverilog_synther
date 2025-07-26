

module tb(

);
logic a_arr[$] = {1,0,0,0,1,0,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,
        0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,
        1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,
        1,0,1,0,1,0,1,0};
logic b_arr[$] = {1,1,0,0,0,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,
        0,1,0,1,0,0,0,0,0,1,1,1,0,1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,1,0,
        0,0,0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,
        0,0,0,1,0,0,0,0};
logic c_arr[$] = {1,1,1,1,1,0,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1};
logic d_arr[$] = {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1};

reg clk, rst;
logic a,b,c,d;

`include "test0.sv"
`include "test1.sv"
`include "test2.sv"
`include "test3.sv"
`include "test4.sv"
`include "test5.sv"
`include "test6.sv"
`include "test7.sv"
`include "test8.sv"
`include "test9.sv"
`include "test10.sv"
`include "test11.sv"
`include "test12.sv"
`include "test13.sv"
`include "test14.sv"
`include "test15.sv"
`include "test16.sv"
`include "test17.sv"
`include "test18.sv"
`include "test19.sv"
`include "test20.sv"
`include "test21.sv"
`include "test22.sv"
`include "test23.sv"
`include "test24.sv"
`include "test25.sv"
`include "test26.sv"
`include "test27.sv"
`include "test28.sv"
`include "test29.sv"
`include "test30.sv"

`include "test100.sv"
`include "test101.sv"
`include "test102.sv"
`include "test103.sv"
`include "test104.sv"
`include "test105.sv"
`include "test106.sv"
`include "test107.sv"
`include "test108.sv"
`include "test109.sv"
`include "test110.sv"
`include "test111.sv"
`include "test112.sv"
`include "test113.sv"
`include "test114.sv"
`include "test115.sv"
`include "test116.sv"
`include "test117.sv"
`include "test118.sv"
`include "test119.sv"
`include "test120.sv"
`include "test121.sv"
`include "test122.sv"
`include "test123.sv"
`include "test124.sv"
`include "test125.sv"
`include "test126.sv"
`include "test127.sv"
`include "test128.sv"
`include "test129.sv"
`include "test130.sv"
`include "test131.sv"
`include "test132.sv"
`include "test133.sv"


initial begin 
    clk = 0;
    forever #5 clk = ~clk;
end

string SV_LOG_FILE_PATH;
int fd;
initial begin 
    a = a_arr[0];
    b = b_arr[0];
    c = c_arr[0];
    d = d_arr[0];
  $value$plusargs("SV_LOG_FILE_PATH=%s", SV_LOG_FILE_PATH);
  $display("[Info] log file is %s\n",SV_LOG_FILE_PATH);
  fd = $fopen(SV_LOG_FILE_PATH,"w+");
  for(int i =0; i < $size(a_arr); i++)begin 
    
    @(posedge clk);
    $fwrite(fd,"run times = %0d\n",i);
    a <= a_arr[i+1];
    b <= b_arr[i+1];
    c <= c_arr[i+1];
    d <= d_arr[i+1];
    
  end
  @(posedge clk);
  $finish(0);
end

initial begin 

    #200000 $finish(0);
end

`ifdef test0
  assert property ( @(posedge clk) s0) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test1
  assert property ( @(posedge clk) s1) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test2
  assert property ( @(posedge clk) s2) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test3
  assert property ( @(posedge clk) s3) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test4
  assert property ( @(posedge clk) s4) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test5
  assert property ( @(posedge clk) s5) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test6
  assert property ( @(posedge clk) s6) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test7
  assert property ( @(posedge clk) s7) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test8
  assert property ( @(posedge clk) s8) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test9
  assert property ( @(posedge clk) s9) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test10
  assert property ( @(posedge clk) s10) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test11
  assert property ( @(posedge clk) s11) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test12
  assert property ( @(posedge clk) s12) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test13
  assert property ( @(posedge clk) s13) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test14
  assert property ( @(posedge clk) s14) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test15
  assert property ( @(posedge clk) s15) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test16
  assert property ( @(posedge clk) s16) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test17
  assert property ( @(posedge clk) s17) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test18
  assert property ( @(posedge clk) s18) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test19
  assert property ( @(posedge clk) s19) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test20
  assert property ( @(posedge clk) s20) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test21
  assert property ( @(posedge clk) s21) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif

`ifdef test22
  assert property ( @(posedge clk) s22) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif

`ifdef test23
  assert property ( @(posedge clk) s23) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif

`ifdef test24
  assert property ( @(posedge clk) s24) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif

`ifdef test25
  assert property ( @(posedge clk) s25) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test26
  assert property ( @(posedge clk) s26) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test27
  assert property ( @(posedge clk) s27) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test28
  assert property ( @(posedge clk) s28) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test29
  assert property ( @(posedge clk) s29) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test30
  assert property ( @(posedge clk) s30) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif

`ifdef test100
  assert property ( @(posedge clk) s100) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test101
  assert property ( @(posedge clk) s101) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test102
  assert property ( @(posedge clk) s102) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test103
  assert property ( @(posedge clk) s103) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test104
  assert property ( @(posedge clk) s104) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test105
  assert property ( @(posedge clk) s105) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test106
  assert property ( @(posedge clk) s106) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test107
  assert property ( @(posedge clk) s107) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test108
  assert property ( @(posedge clk) s108) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test109
  assert property ( @(posedge clk) s109) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test110
  assert property ( @(posedge clk) s110) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test111
  assert property ( @(posedge clk) s111) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test112
  assert property ( @(posedge clk) s112) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test113
  assert property ( @(posedge clk) s113) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test114
  assert property ( @(posedge clk) s114) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test115
  assert property ( @(posedge clk) s115) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test116
  assert property ( @(posedge clk) s116) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test117
  assert property ( @(posedge clk) s117) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test118
  assert property ( @(posedge clk) s118) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test119
  assert property ( @(posedge clk) s119) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test120
  assert property ( @(posedge clk) s120) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test121
  assert property ( @(posedge clk) s121) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test122
  assert property ( @(posedge clk) s122) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test123
  assert property ( @(posedge clk) s123) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test124
  assert property ( @(posedge clk) s124) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test125
  assert property ( @(posedge clk) s125) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test126
  assert property ( @(posedge clk) s126) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test127
  assert property ( @(posedge clk) s127) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test128
  assert property ( @(posedge clk) s128) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test129
  assert property ( @(posedge clk) s129) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test130
  assert property ( @(posedge clk) s130) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test131
  assert property ( @(posedge clk) s131) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test132
  assert property ( @(posedge clk) s132) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif
`ifdef test133
  assert property ( @(posedge clk) s133) begin
      $fwrite(fd,"finish\n");
    end
    else begin 
      $fwrite(fd,"error\n");
    end
`endif




































endmodule


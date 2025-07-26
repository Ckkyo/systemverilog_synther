

module tb(

);

initial
	begin
		$fsdbDumpfile("wave.fsdb");  //记录波形，波形名字testname.fsdb
		$fsdbDumpvars("+all");  //+all参数，dump SV中的struct结构体
		$fsdbDumpSVA();   //将assertion的结果存在fsdb中
		$fsdbDumpMDA(0, tb);  //dump memory arrays
		//0: 当前级及其下面所有层级，如top.A, top.A.a，所有在top下面的多维数组均会被dump
		//1: 仅仅dump当前组，也就是说，只dump top这一层的多维数组。
	end


reg sys_clk, sys_rst;
initial begin 
    sys_clk = 0;
    forever #5 sys_clk = ~sys_clk;
end
initial begin 
  sys_rst = 1;
  @(posedge sys_clk);
  @(posedge sys_clk);
  sys_rst <= 0;
end


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

reg gclk, grst;
logic a,b,c,d;

initial begin 
    gclk = 0;
    wait(sys_rst === 0);
    forever begin
      repeat(50) @(posedge sys_clk);
      gclk <= ~gclk;
    end
end
initial begin 
  grst = 1;
  grst = 0;
  @(posedge gclk);
  @(posedge gclk);
end


int fd;
string SV_LOG_FILE_PATH;
initial begin 
  $value$plusargs("SV_LOG_FILE_PATH=%s", SV_LOG_FILE_PATH);
  $display("[Info] log file is %s\n",SV_LOG_FILE_PATH);
  fd = $fopen(SV_LOG_FILE_PATH,"w+");

  wait(grst===0);
  // @(posedge gclk);
  a = a_arr[0];
  b = b_arr[0];
  c = c_arr[0];
  d = d_arr[0];
  for(int i =0; i < $size(a_arr); i++)begin 
    
    @(posedge gclk);
    $fwrite(fd,"run times = %0d\n",i);
    a <= a_arr[i+1];
    b <= b_arr[i+1];
    c <= c_arr[i+1];
    d <= d_arr[i+1];
    
  end
  @(posedge gclk);
  $finish(0);
end

{{module_name}} {{module_name}}(
    .sys_clk(sys_clk),  // 系统时钟
    .sys_rst(sys_rst),  // 系统复位
    .busy(),    // 状态机正在计算
    .file_fd(fd),

    {%-for _, elem in enumerate(sva_all_input_signals)%}
        {%- if elem != "__delay1" %}
    .{{elem}}({{elem}}),
        {%- endif%}
    {%-endfor%}

    .gclk(gclk),     // 用户时钟
    .grst(grst)      // 用户复位
);

// initial begin 

//     #200000 $finish(0);
// end

endmodule


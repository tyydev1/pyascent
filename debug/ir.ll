; ModuleID = "main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

@"true" = constant i1 1
@"false" = constant i1 0
define i32 @"ret_o"()
{
ret_o_entry:
  %".2" = alloca i32
  store i32 0, i32* %".2"
  %".4" = load i32, i32* %".2"
  ret i32 %".4"
}

define i32 @"main"()
{
main_entry:
  %".2" = alloca i32
  store i32 64, i32* %".2"
  %".4" = load i32, i32* %".2"
  %".5" = sdiv i32 %".4", 2
  %".6" = mul i32 16, 2
  %".7" = sub i32 %".5", %".6"
  store i32 %".7", i32* %".2"
  %".9" = load i32, i32* %".2"
  %".10" = add i32 %".9", 1
  %".11" = alloca i32
  store i32 %".10", i32* %".11"
  %".13" = load i32, i32* %".11"
  %".14" = load i32, i32* %".2"
  %".15" = sub i32 %".14", 10
  %".16" = add i32 %".13", %".15"
  %".17" = alloca i32
  store i32 %".16", i32* %".17"
  %".19" = load i32, i32* %".17"
  %".20" = icmp ne i32 %".19", 0
  br i1 %".20", label %"main_entry.if", label %"main_entry.else"
main_entry.if:
  %".22" = load i32, i32* %".17"
  store i32 %".22", i32* %".17"
  br label %"main_entry.endif"
main_entry.else:
  %".25" = load i32, i32* %".17"
  %".26" = sub i32 8, 3
  %".27" = mul i32 %".26", 2
  %".28" = add i32 %".25", %".27"
  %".29" = sub i32 %".28", 1
  store i32 %".29", i32* %".17"
  br label %"main_entry.endif"
main_entry.endif:
  %".32" = call i32 @"ret_o"()
  ret i32 %".32"
}

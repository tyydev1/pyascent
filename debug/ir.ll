; ModuleID = "main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

define float @"main"()
{
main_entry:
  %".2" = alloca float
  store float 0x40515ae140000000, float* %".2"
  %".4" = load float, float* %".2"
  ret float %".4"
}

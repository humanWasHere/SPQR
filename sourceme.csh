if (`domainname` == "ratmpw") then
    setenv PYTHONPATH /work/retprod/src/pythonlib
else if (`domainname` == "azurl") then
    setenv PYTHONPATH /prj/ret/retprod/src
else
    unsetenv PYTHONPATH
endif
source /sw/st/itcad/setup/global/sw -set .ucdprod

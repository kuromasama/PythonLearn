#include <iostream>
#include <vector>
using namespace std;

int main(){
        int a,c=0;
        vector<int> v;
        while(cin >> a)v.push_back(a);
        for(int i=0; i<v.size();i++){
                for(int j=i;j<v.size();j++){
                        c=j-1;
                }
        }
        cout << c;
    system("pause");
}
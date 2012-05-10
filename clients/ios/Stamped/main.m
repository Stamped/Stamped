//
//  main.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/5/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STAppDelegate.h"
#import "STConfiguration.h"
#import "Util.h"

int main(int argc, char* argv[]) {
  @try {
    
    if ([[STConfiguration sharedInstance] internalVersion] > 0) {
      @autoreleasepool {
        return UIApplicationMain(argc, argv, nil, NSStringFromClass([STAppDelegate class]));
      }
    }
    else {
      NSAutoreleasePool* pool = [[NSAutoreleasePool alloc] init];
      int retVal = UIApplicationMain(argc, argv, nil, nil);
      [pool release];
      return retVal;
    }
  }
  @catch (NSException *exception) {
    [Util logOperationException:exception withMessage:@"Main application error"];
  }
  @finally {
  }
}

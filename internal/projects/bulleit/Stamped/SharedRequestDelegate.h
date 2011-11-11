//
//  SharedRequestDelegate.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/20/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "FBConnect.h"

@interface SharedRequestDelegate : NSObject <RKObjectLoaderDelegate, RKRequestDelegate, FBSessionDelegate, FBRequestDelegate>

+ (SharedRequestDelegate*)sharedDelegate;
- (void)fbDidLogin;

@end

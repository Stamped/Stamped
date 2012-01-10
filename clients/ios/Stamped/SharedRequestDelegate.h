//
//  SharedRequestDelegate.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/20/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>

@interface SharedRequestDelegate : NSObject <RKObjectLoaderDelegate>

+ (SharedRequestDelegate*)sharedDelegate;

@end

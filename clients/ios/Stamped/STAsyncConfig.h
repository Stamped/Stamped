//
//  STAsyncConfig.h
//  Stamped
//
//  Created by Landon Judkins on 3/15/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STAsyncConfig <NSObject>

@property (nonatomic, readonly) NSOperationQueue* asyncQueue;

@end

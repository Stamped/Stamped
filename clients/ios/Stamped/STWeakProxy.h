//
//  STWeakProxy.h
//  Stamped
//
//  Created by Landon Judkins on 3/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface STWeakProxy : NSObject

- (id)initWithValue:(id)value;

@property (nonatomic, readwrite, assign) id value;

@end

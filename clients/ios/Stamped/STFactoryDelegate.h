//
//  STFactoryDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 3/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STFactoryDelegate <NSObject>

- (void)didLoad:(id)object withLabel:(id)label;

@end

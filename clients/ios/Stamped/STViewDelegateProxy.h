//
//  STViewDelegateProxy.h
//  Stamped
//
//  Created by Landon Judkins on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STViewDelegate.h"

@interface STViewDelegateProxy : NSObject <STViewDelegate>

@property (nonatomic, assign) id<STViewDelegate> delegate;

@end

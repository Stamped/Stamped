//
//  STViewDelegateDependent.h
//  Stamped
//
//  Created by Landon Judkins on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STViewDelegate;

@protocol STViewDelegateDependent <NSObject>

@property (nonatomic, readwrite, assign) id<STViewDelegate> delegate;

@end

//
//  STViewDelegate.h
//  Stamped
//
//  Created by Landon Judkins on 3/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STFactoryDelegate.h"
#import "STResizeDelegate.h"
#import "STAction.h"


@protocol STViewDelegate <STFactoryDelegate, STResizeDelegate>

- (void)didChooseAction:(id<STAction>)action;
- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action;

@property (nonatomic, readonly) NSOperationQueue* asyncQueue;

@end

typedef UIView* (^STViewCreator)(id<STViewDelegate>);
typedef void (^STViewCreatorCallback)(STViewCreator);
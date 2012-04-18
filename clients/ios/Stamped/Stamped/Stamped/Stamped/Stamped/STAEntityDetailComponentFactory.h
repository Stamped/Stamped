//
//  STAEntityDetailComponentFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STEntityDetailComponentFactory.h"

@interface STAEntityDetailComponentFactory : NSObject <STEntityDetailComponentFactory>

- (id)generateAsynchronousState:(id<STEntityDetail>)anEntityDetail withOperation:(NSOperation*)operation;

- (UIView*)generateViewOnMainLoop:(id<STEntityDetail>)anEntityDetail
                        withState:(id)asyncState
                      andDelegate:(id<STViewDelegate>)delegate;

@end

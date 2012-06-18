//
//  STBlockUIView.m
//  Stamped
//
//  Created by Devin Doty on 5/15/12.
//
//

#import "STBlockUIView.h"

@implementation STBlockUIView
@synthesize drawingHandler=_drawingHandler;

- (void)drawRect:(CGRect)rect {
    if (_drawingHandler) {
        _drawingHandler(UIGraphicsGetCurrentContext(), rect);
    }
}

- (void)dealloc {
    self.drawingHandler = nil;
    [super dealloc];
}

@end

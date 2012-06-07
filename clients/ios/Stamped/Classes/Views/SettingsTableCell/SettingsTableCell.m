//
//  SettingsTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/7/12.
//
//

#import "SettingsTableCell.h"

@implementation SettingsTableCell

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if (self = [super initWithStyle:style reuseIdentifier:reuseIdentifier]) {
    
        
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        background.backgroundColor = [UIColor clearColor];
        [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
            
            CGPathRef path = [UIBezierPath bezierPathWithRoundedRect:CGRectInset(rect, 10, 0) cornerRadius:4.0f].CGPath;
            CGContextAddPath(ctx, path);
            CGContextFillPath(ctx);
            
        }];
        
        [self addSubview:background];
        [background release];
        self.backgroundView = background;
        
        
        UIImageView *view = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"st_cell_arrow.png"] highlightedImage:[UIImage imageNamed:@"st_cell_arrow_hi.png"]];
        self.accessoryView = view;
        [view release];
        
    
    }
    return self;
}

- (void)setBackgroundFrame:(CGRect)frame {
    
    
    
    
}


- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
}

@end

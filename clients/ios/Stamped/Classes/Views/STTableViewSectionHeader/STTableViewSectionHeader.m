//
//  STTableHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import "STTableViewSectionHeader.h"

@implementation STTableViewSectionHeader

- (id)initWithFrame:(CGRect)frame {
    
    frame.size.height = [[self class] height];
    
    if (self = [super initWithFrame:frame]) {

        UIImage *image = [UIImage imageNamed:@"find_friends_section_header_bg.png"];
        self.image = [image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0];
        self.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        
        UIFont *font = [UIFont boldSystemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(10.0f, floorf((self.bounds.size.height-font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.font = font;
        label.textColor = [UIColor whiteColor];
        label.backgroundColor = [UIColor clearColor];
        label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.2f];
        label.shadowOffset = CGSizeMake(0.0f, -1.0f);
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];
    
    }
    return self;
}

- (void)dealloc {
    [_titleLabel release], _titleLabel=nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [_titleLabel sizeToFit];
    
    CGRect frame = _titleLabel.frame;
    frame.size.width = MIN(frame.size.width, self.bounds.size.width - 20.0f);
    _titleLabel.frame = frame;
    
}

+ (CGFloat)height {
    return 25.0f;
}

@end
